"""Test window functions."""
import numpy as np
import xarray as xr

from frites.conn import (conn_reshape_undirected, conn_reshape_directed,
                         conn_ravel_directed, define_windows, plot_windows,
                         conn_dfc, conn_covgc, conn_get_pairs)


class TestConnUtils(object):

    def test_conn_reshape_undirected(self):
        """Test function conn_reshape_undirected."""
        import pandas as pd
        # compute DFC
        n_epochs, n_times, n_roi = 5, 100, 3
        times = np.linspace(-1, 1, n_times)
        win_sample = np.array([[10, 20], [30, 40]])
        roi = [f"roi_{k}" for k in range(n_roi)]
        order = ['roi_2', 'roi_1']
        x = np.random.rand(n_epochs, n_roi, n_times)
        dfc = conn_dfc(x, win_sample, times=times, roi=roi).mean('trials')
        # reshape it without the time dimension
        dfc_mean = conn_reshape_undirected(dfc.mean('times'))
        assert dfc_mean.shape == (n_roi, n_roi, 1)
        df = conn_reshape_undirected(dfc.mean('times'), order=order,
                                     to_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        # reshape it with the time dimension
        dfc_times = conn_reshape_undirected(dfc.copy())
        assert dfc_times.shape == (n_roi, n_roi, len(dfc['times']))
        # try the reorder
        dfc_order = conn_reshape_undirected(dfc, order=order)
        assert dfc_order.shape == (2, 2, len(dfc['times']))
        assert np.array_equal(dfc_order['sources'], dfc_order['targets'])
        assert np.array_equal(dfc_order['sources'], order)

    def test_conn_reshape_directed(self):
        """Test function conn_reshape_directed."""
        n_epochs, n_times, n_roi = 5, 100, 3
        x = np.random.rand(n_epochs, n_roi, n_times)
        dt, lag, t0 = 10, 2, [50, 80]
        order = ['roi_2', 'roi_1']
        # compute covgc
        gc = conn_covgc(x, dt, lag, t0, n_jobs=1, method='gauss')
        gc = gc.mean('trials')
        # reshape it without the time dimension
        gc_mean = conn_reshape_directed(gc.copy().mean('times'))
        assert gc_mean.shape == (n_roi, n_roi, 1)
        # reshape it with the time dimension
        gc_times = conn_reshape_directed(gc.copy())
        assert gc_times.shape == (n_roi, n_roi, len(gc['times']))
        # try the reorder
        gc_order = conn_reshape_directed(gc.copy(), order=order)
        assert gc_order.shape == (2, 2, len(gc['times']))
        assert np.array_equal(gc_order['sources'], gc_order['targets'])
        assert np.array_equal(gc_order['sources'], order)

    def test_define_windows(self):
        """Test function define_windows."""
        n_pts = 1000
        times = np.linspace(-1, 1, n_pts, endpoint=True)
        kw = dict(verbose=False)

        # ---------------------------------------------------------------------
        # full window
        # ---------------------------------------------------------------------
        ts = define_windows(times, **kw)[0]
        np.testing.assert_array_equal(ts, np.array([[0, n_pts - 1]]))

        # ---------------------------------------------------------------------
        # custom windows
        # ---------------------------------------------------------------------
        # single window
        win = [0, .5]
        ts = define_windows(times, windows=win, **kw)[0]
        np.testing.assert_almost_equal(times[ts.ravel()], win, decimal=2)
        # multiple
        win = [[-.5, -.1], [-.1, 0.], [0, .5]]
        ts = define_windows(times, windows=win, **kw)[0]
        np.testing.assert_almost_equal(times[ts], np.array(win), decimal=2)

        # ---------------------------------------------------------------------
        # sliding windows
        # ---------------------------------------------------------------------
        # length only
        ts = define_windows(times, slwin_len=.1, **kw)[0]
        tts = times[ts]
        ttsd = np.diff(tts, axis=1)
        np.testing.assert_almost_equal(ttsd, np.full_like(ttsd, .1), decimal=2)
        # with starting point
        ts = define_windows(times, slwin_len=.1, slwin_start=.5, **kw)[0]
        np.testing.assert_almost_equal(times[ts][0, 0], .5, decimal=2)
        # with stoping point
        ts = define_windows(times, slwin_len=.1, slwin_stop=.9,
                            **kw)[0]
        assert times[ts][-1, -1] <= .9
        # with step between temporal windows
        ts = define_windows(times, slwin_len=.1, slwin_step=.2, **kw)[0]
        tts = times[ts]
        ttsd = np.diff(tts, axis=0)
        np.testing.assert_almost_equal(ttsd, np.full_like(ttsd, .2), decimal=2)

    def test_plot_windows(self):
        """Test function plot_windows."""
        n_pts = 1000
        times = np.linspace(-1, 1, n_pts, endpoint=True)
        kw = dict(verbose=False)
        ts = define_windows(times, slwin_len=.1, **kw)[0]
        plot_windows(times, ts)

    def test_conn_get_pairs(self):
        """Test function conn_get_pairs."""
        roi = [np.array(['r1', 'r0']), np.array(['r0', 'r2', 'r1'])]
        # test non-directed
        df, _ = conn_get_pairs(roi, directed=False)
        rundir = np.c_[['r0', 'r0', 'r1'], ['r1', 'r2', 'r2']]
        names = [f'{k}-{i}' for k, i in zip(rundir[:, 0], rundir[:, 1])]
        suj = [0, 1, 1, 1]
        nsuj = [2, 1, 1]
        assert np.all(df['keep'])
        np.testing.assert_array_equal(df['sources'], rundir[:, 0])
        np.testing.assert_array_equal(df['targets'], rundir[:, 1])
        np.testing.assert_array_equal(df['#subjects'], nsuj)
        np.testing.assert_array_equal(df['names'], names)
        np.testing.assert_array_equal(np.concatenate(df['subjects']), suj)
        # test directed
        df, _ = conn_get_pairs(roi, directed=True)
        rdir = np.c_[['r0', 'r0', 'r1', 'r1', 'r2', 'r2'],
                     ['r1', 'r2', 'r0', 'r2', 'r0', 'r1']]
        names = [f'{k}->{i}' for k, i in zip(rdir[:, 0], rdir[:, 1])]
        suj = [0, 1, 1, 0, 1, 1, 1, 1]
        nsuj = [2, 1, 2, 1, 1, 1]
        assert np.all(df['keep'])
        np.testing.assert_array_equal(df['sources'], rdir[:, 0])
        np.testing.assert_array_equal(df['targets'], rdir[:, 1])
        np.testing.assert_array_equal(df['#subjects'], nsuj)
        np.testing.assert_array_equal(df['names'], names)
        np.testing.assert_array_equal(np.concatenate(df['subjects']), suj)
        # test nb_min_suj filtering (non-directed)
        df, _ = conn_get_pairs(roi, directed=False, nb_min_suj=2)
        np.testing.assert_array_equal(df['keep'], [True, False, False])
        df = df.loc[df['keep']]
        np.testing.assert_array_equal(df['sources'], ['r0'])
        np.testing.assert_array_equal(df['targets'], ['r1'])
        np.testing.assert_array_equal(df['#subjects'], [2])
        np.testing.assert_array_equal(np.concatenate(df['subjects']), [0, 1])
        np.testing.assert_array_equal(df['names'], ['r0-r1'])
        # test nb_min_suj filtering (directed)
        df, _ = conn_get_pairs(roi, directed=True, nb_min_suj=2)
        np.testing.assert_array_equal(
            df['keep'], [True, False, True, False, False, False])
        df = df.loc[df['keep']]
        np.testing.assert_array_equal(df['sources'], ['r0', 'r1'])
        np.testing.assert_array_equal(df['targets'], ['r1', 'r0'])
        np.testing.assert_array_equal(df['#subjects'], [2, 2])
        np.testing.assert_array_equal(
            np.concatenate(list(df['subjects'])), [0, 1, 0, 1])
        np.testing.assert_array_equal(df['names'], ['r0->r1', 'r1->r0'])

    def test_conn_ravel_directed(self):
        """Test function conn_ravel_directed."""
        n_trials = 100
        n_times = 1000
        n_roi = 3
        x_s, x_t = np.triu_indices(n_roi, k=1)

        # build coordinates
        roi = [f'r{s}-r{t}' for s, t in zip(x_s, x_t)]
        trials = np.random.randint(0, 2, (n_trials,))
        times = np.arange(n_times) / 64.
        direction = ['x->y', 'y->x']
        roi_dir = ['r0->r1', 'r0->r2', 'r1->r2', 'r1->r0', 'r2->r0', 'r2->r1']

        # create the connectivity arrays
        conn_xy = np.random.rand(n_trials, n_roi, n_times)
        conn_yx = np.random.rand(n_trials, n_roi, n_times)
        conn_c = np.concatenate((conn_xy, conn_yx), axis=1)

        # stack them and xarray conversion
        conn = np.stack((conn_xy, conn_yx), axis=-1)
        conn = xr.DataArray(conn, dims=('trials', 'roi', 'times', 'direction'),
                            coords=(trials, roi, times, direction))

        # ravel the array
        conn_r = conn_ravel_directed(conn)
        assert len(conn_r.shape) == 3
        np.testing.assert_array_equal(conn_r['roi'].data, roi_dir)
        np.testing.assert_array_equal(conn_r.data, conn_c)
